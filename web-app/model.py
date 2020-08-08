import torch
import torch.nn as nn

class DNN1(nn.Module):
    def __init__(self,resnet_path,nclasses,labels):
        super(DNN1, self).__init__()
        #number of multi-labels
        self.labels=labels
        #no of out_features forr each label
        self.nclasses=nclasses
        self.nmid_ft=512
        
        #Resnet model
        self.resnet=torch.load(resnet_path)
        #input channels of our classifier
        in_features = self.resnet.fc.in_features
        self.dropout=nn.Dropout(0.2)
        
        #Removing the pretrained classifier layer and freezing the weights
        self.resnet = nn.Sequential(*(list(self.resnet.children())[:-1]))
        for param in self.resnet.parameters():
            param.requires_grad = False
            
        #building our own classifier for each label
        self.fc1=nn.Linear(in_features,self.nmid_ft)
        
        
        self.classifier = nn.ModuleDict()
        for label in labels:
            self.classifier[label]=nn.Linear(self.nmid_ft,nclasses[label])
        #Since we are dealing with multi-label each with mutli-class classification

            
    def forward(self,x):
        """
        for the forward pass of the model, the input image will pass through resnet FCNN
        then it will be flattened and there will be n parallel Dense layer for each label.
        then loss function will be crossentropy which has inbuilt softmax function
        """
        x=torch.relu(self.fc1(self.resnet(x).view(x.shape[0],-1)))
        x=self.dropout(x)
        y=dict()
        for label in self.classifier.keys():
            y[label]=self.classifier[label](x)
        return y